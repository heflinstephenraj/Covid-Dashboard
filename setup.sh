mkdir -p ~/.streamlit

echo "[theme]
primaryColor='#ff0004'
backgroundColor='#ffffff'
secondaryBackgroundColor='#dce2ec'
textColor='#000000'
font='sans serif'


[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml