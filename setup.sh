mkdir -p ~/.streamlit

echo '[theme]
primaryColor="#f63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#f0f2f6"
textColor="#262730"
font="sans serif"
[server]
headless = true
port = $PORT
enableCORS = false
' > ~/.streamlit/config.toml