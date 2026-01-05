import json
import base64
import io
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def handler(event, context):
    try:
        if event.get('httpMethod') != 'POST':
            return {
                'statusCode': 405,
                'body': 'Method Not Allowed'
            }

        body = event.get('body')
        if not body:
            return {'statusCode': 400, 'body': 'No data provided'}

        data = json.loads(body)
        
        # Normalize data input: check if it's a list or a dict with a key
        messages = []
        if isinstance(data, list):
            messages = data
        elif isinstance(data, dict):
            # Try common keys
            for key in ['messages', 'data', 'chat_history']:
                if key in data and isinstance(data[key], list):
                    messages = data[key]
                    break
            if not messages:
                # If no known key, maybe the dict values are the rows? unlikely but possible
                # Fallback: assume the dict itself is the structure if it has lists as columns
                try:
                    df_test = pd.DataFrame(data)
                    messages = df_test.to_dict(orient='records')
                except:
                    return {'statusCode': 400, 'body': 'Could not parse message list from JSON'}

        if not messages:
             return {'statusCode': 400, 'body': 'No messages found'}

        # Create DataFrame
        df = pd.DataFrame(messages)

        # map column names to standard ones if possible
        # Target: timestamp, content, sender
        col_map = {}
        for col in df.columns:
            lower_col = col.lower()
            if 'time' in lower_col:
                col_map[col] = 'timestamp'
            elif 'content' in lower_col or 'message' in lower_col or 'text' in lower_col:
                col_map[col] = 'content'
            elif 'send' in lower_col or 'author' in lower_col or 'user' in lower_col:
                col_map[col] = 'sender'
        
        df = df.rename(columns=col_map)
        
        # Ensure we have required columns
        required = ['timestamp', 'sender']
        if not all(col in df.columns for col in required):
             return {'statusCode': 400, 'body': f'Missing required columns (timestamp, sender). Found: {list(df.columns)}'}

        # Process Timestamp
        # Check if it's ms or seconds or string
        try:
            # If numeric and looks like ms (year 1970+)
            if pd.api.types.is_numeric_dtype(df['timestamp']):
                if df['timestamp'].max() > 10000000000: # likely ms
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                else:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
        except Exception as e:
            return {'statusCode': 400, 'body': f'Error parsing timestamps: {str(e)}'}

        # --- Analysis ---
        
        stats = {}
        stats['total_messages'] = len(df)
        
        # Top sender
        sender_counts = df['sender'].value_counts()
        stats['top_sender'] = sender_counts.index[0] if not sender_counts.empty else "N/A"
        
        # Busiest Day
        day_counts = df['timestamp'].dt.date.value_counts()
        stats['busiest_day'] = str(day_counts.index[0]) if not day_counts.empty else "N/A"

        # --- Visualizations ---
        plt.style.use('dark_background')
        chart_images = {}

        # 1. Sender Pie Chart
        plt.figure(figsize=(6, 6))
        # Limit to top 5 + Others
        top_senders = sender_counts.head(5)
        if len(sender_counts) > 5:
            others = pd.Series([sender_counts[5:].sum()], index=['Others'])
            top_senders = pd.concat([top_senders, others])
        
        plt.pie(top_senders, labels=top_senders.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Accent.colors)
        plt.title('Message Distribution')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True)
        buf.seek(0)
        chart_images['sender_pie'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        # 2. Hourly Activity
        plt.figure(figsize=(10, 6))
        hourly_counts = df['timestamp'].dt.hour.value_counts().sort_index()
        # Fill missing hours
        hourly_counts = hourly_counts.reindex(range(24), fill_value=0)
        
        plt.bar(hourly_counts.index, hourly_counts.values, color='#1db954', alpha=0.7)
        plt.xlabel('Hour of Day (0-23)')
        plt.ylabel('Message Count')
        plt.title('Activity by Hour')
        plt.xticks(range(0, 24, 2))
        plt.grid(axis='y', alpha=0.3)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True)
        buf.seek(0)
        chart_images['hourly_bar'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        # 3. Daily Activity (Line Chart)
        plt.figure(figsize=(10, 6))
        daily_counts = df['timestamp'].dt.date.value_counts().sort_index()
        
        plt.plot(daily_counts.index, daily_counts.values, color='#1db954', linewidth=2, marker='o', markersize=4)
        plt.xlabel('Date')
        plt.ylabel('Messages')
        plt.title('Daily Message Volume')
        plt.grid(alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True)
        buf.seek(0)
        chart_images['daily_line'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        # 4. Average Message Length (Horizontal Bar)
        df['length'] = df['content'].fillna('').astype(str).str.len()
        avg_len = df.groupby('sender')['length'].mean().sort_values(ascending=True).tail(5)
        
        plt.figure(figsize=(10, 6))
        plt.barh(avg_len.index, avg_len.values, color='#9b59b6', alpha=0.8)
        plt.xlabel('Average Characters per Message')
        plt.title('Who types the longest messages?')
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True)
        buf.seek(0)
        chart_images['avg_len_bar'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        stats['charts'] = chart_images

        # Serialize results
        # Use a custom encoder or just stringify the known types
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
