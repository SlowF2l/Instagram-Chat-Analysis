# Instagram Chat Recap Generator

I have created a complete "Spotify Wrapped" style application for analyzing Instagram chat history.

## Features implemented:
1.  **Web Interface**: A responsive, dark-mode frontend that mimics the "Recap" experience.
    *   **Interactive Slides**: Users scroll through their statistics with smooth fade transitions.
    *   **Privacy-First**: Files are processed in a serverless function and results are displayed immediately.
2.  **Python Backend Analysis**:
    *   Built a **Netlify Function** (`analyze.py`) using Python.
    *   Utilized **Pandas** for robust data processing of JSON chat logs.
    *   Utilized **Matplotlib** to generate high-quality statistical charts on the fly.
3.  **Visualizations**:
    *   **Message Volume**: Total message count.
    *   **Top Talker**: Pie chart showing the distribution of messages per sender.
    *   **Peak Hours**: Bar chart showing activity by hour of the day.
    *   **Chat History Timeline**: Line chart showing message volume over time.
    *   **Longest Typer**: Bar chart comparing average message length per sender.
    *   **Fun Facts**: Highlights busiest days and top senders.

## Technical Details:
-   **Frontend**: HTML5, CSS3 (Flexbox/Grid, Animations), Vanilla JavaScript.
-   **Backend**: Python 3.8+ (Netlify Functions).
-   **Libraries**: `pandas`, `matplotlib`, `numpy`, `plotnine` (included in requirements).
-   **Configuration**: `netlify.toml` set up for easy deployment.

## How to use:
1.  Deploy the site to Netlify.
2.  Open the site URL.
3.  Upload an Instagram chat JSON file (usually found in `messages/inbox/.../message_1.json` from your data download).
4.  Enjoy the recap!