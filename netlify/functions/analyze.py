import json
import base64
import io
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

def handler(event, context):
    try:
        # Increase limit for large plots if needed
        plt.rcParams['figure.max_open_warning'] = 20

        if event.get('httpMethod') != 'POST':
            return {
                'statusCode': 405,
                'body': 'Method Not Allowed'
            }

        body = event.get('body')
        if not body:
            return {'statusCode': 400, 'body': 'No data provided'}

        data = json.loads(body)
        
        # --- Data Parsing Logic ---
        messages = []
        if isinstance(data, list):
            messages = data
        elif isinstance(data, dict):
            # Try to find the list of messages
            for key in ['messages', 'data', 'chat_history']:
                if key in data and isinstance(data[key], list):
                    messages = data[key]
                    break
            if not messages and 'participants' in data: # Common Instagram export format
                 # Sometimes it's just in the root if not named 'messages' but that's rare for IG
                 pass

        if not messages:
             return {'statusCode': 400, 'body': 'No messages found in the provided JSON'}

        df = pd.DataFrame(messages)

        # --- Column Mapping ---
        # We need 'sender' and 'timestamp' and 'content'
        col_map = {}
        for col in df.columns:
            lower = col.lower()
            if 'sender_name' in lower:
                col_map[col] = 'sender'
            elif 'timestamp' in lower: # timestamp_ms or timestamp
                col_map[col] = 'timestamp'
            elif 'content' in lower and 'original' not in lower:
                col_map[col] = 'content'
        
        df = df.rename(columns=col_map)
        
        if 'sender' not in df.columns or 'timestamp' not in df.columns:
            return {'statusCode': 400, 'body': f'Could not identify sender or timestamp columns. Found: {list(df.columns)}'}

        # --- Timestamp Cleaning ---
        # Handle ms vs seconds. 
        # If max timestamp > 30000000000, it's definitely ms (year 2920)
        # 1672531200000 is 2023 in ms. 1672531200 is 2023 in s.
        try:
            ts_max = df['timestamp'].max()
            if pd.api.types.is_numeric_dtype(df['timestamp']):
                if ts_max > 10000000000: 
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                else:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            else:
                # Iso string or similar
                df['timestamp'] = pd.to_datetime(df['timestamp'])
        except Exception as e:
            return {'statusCode': 400, 'body': f'Timestamp parse error: {str(e)}'}

        # Drop invalid timestamps
        df = df.dropna(subset=['timestamp'])

        # --- Statistics Generation ---
        stats = {}
        stats['total_messages'] = len(df)
        
        sender_counts = df['sender'].value_counts()
        stats['top_sender'] = sender_counts.index[0] if not sender_counts.empty else "Ghost"
        
        # Time extraction
        df['hour'] = df['timestamp'].dt.hour
        df['date'] = df['timestamp'].dt.date
        df['weekday'] = df['timestamp'].dt.day_name()
        df['weekday_idx'] = df['timestamp'].dt.weekday # 0=Monday, 6=Sunday

        day_counts = df['date'].value_counts()
        if not day_counts.empty:
            stats['busiest_day'] = day_counts.idxmax().strftime('%Y-%m-%d')
            stats['max_msgs_one_day'] = int(day_counts.max())
        else:
            stats['busiest_day'] = "N/A"
            stats['max_msgs_one_day'] = 0

        # --- Visualizations ---
        # We will use dark style for all
        plt.style.use('dark_background')
        chart_images = {}

        # Helper to save plot
        def save_plot(name):
            buf = io.BytesIO()
            plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
            buf.seek(0)
            chart_images[name] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()

        # 1. Pie Chart: Message Distribution
        # This code produces a Pie Chart using Matplotlib
        plt.figure(figsize=(7, 7))
        top_senders = sender_counts.head(5)
        if len(sender_counts) > 5:
            others = pd.Series([sender_counts[5:].sum()], index=['Others'])
            top_senders = pd.concat([top_senders, others])
        
        # Use a qualitative colormap
        colors = plt.cm.Set3.colors
        plt.pie(top_senders, labels=top_senders.index, autopct='%1.1f%%', startangle=140, colors=colors)
        plt.title('Who dominates the chat?')
        save_plot('sender_pie')

        # 2. Bar Chart: Activity by Hour
        # This code produces a Bar Chart using Matplotlib
        plt.figure(figsize=(10, 6))
        hourly_counts = df['hour'].value_counts().sort_index()
        hourly_counts = hourly_counts.reindex(range(24), fill_value=0)
        
        plt.bar(hourly_counts.index, hourly_counts.values, color='#1db954', alpha=0.8)
        plt.xlabel('Hour of Day')
        plt.ylabel('Messages')
        plt.title('When are you most active?')
        plt.xticks(range(0, 24, 2))
        plt.grid(axis='y', alpha=0.2)
        save_plot('hourly_bar')

        # 3. Line Chart: Timeline
        # This code produces a Line Chart using Matplotlib
        plt.figure(figsize=(10, 6))
        daily_counts = df.groupby('date').size()
        
        plt.plot(daily_counts.index, daily_counts.values, color='#1db954', linewidth=1.5)
        plt.fill_between(daily_counts.index, daily_counts.values, color='#1db954', alpha=0.2)
        plt.xlabel('Date')
        plt.ylabel('Messages')
        plt.title('Chat History Volume')
        plt.grid(alpha=0.2)
        plt.xticks(rotation=45)
        save_plot('daily_line')

        # 4. Heatmap: Day of Week vs Hour
        # This code produces a Heatmap using Seaborn
        plt.figure(figsize=(10, 6))
        # Create a crosstab: Index=Day, Columns=Hour
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = pd.crosstab(df['weekday'], df['hour'])
        heatmap_data = heatmap_data.reindex(days_order)
        heatmap_data = heatmap_data.reindex(columns=range(24), fill_value=0)
        
        sns.heatmap(heatmap_data, cmap='viridis', cbar_kws={'label': 'Message Count'})
        plt.title('Weekly Activity Heatmap')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        save_plot('heatmap')

        # 5. Bar Plot: Average Message Length
        # This code produces a Horizontal Bar Chart using Matplotlib
        if 'content' in df.columns:
            df['length'] = df['content'].fillna('').astype(str).str.len()
            avg_len = df.groupby('sender')['length'].mean().sort_values(ascending=True).tail(10)
            
            plt.figure(figsize=(10, 6))
            # Use seaborn color palette for bars
            sns_colors = sns.color_palette("husl", len(avg_len))
            plt.barh(avg_len.index, avg_len.values, color=sns_colors)
            plt.xlabel('Avg Characters')
            plt.title('Who writes essays?')
            save_plot('avg_len_bar')

        stats['charts'] = chart_images

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(stats, default=str)
        }

    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e), 'trace': traceback.format_exc()})
        }