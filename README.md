# CatGPT
Personally customized ChatGPT

# Usage
First, install the requirements:
```
pip install -r requirements.txt
```
And set the environment variable `OPENAI_API_KEY` to your [OpenAI API](https://platform.openai.com/account/api-keys) key (recommended to add it to your `.bashrc` or `.zshrc` file).
Then, run the script:
```
python terminal.py
```
Or, if you want to use the web interface:
```
python web.py username port
```
and then go to `http://localhost:port` in your browser.
For windows users, you need to run windows-cmd-run.bat instead (replace the username, port and api key with your own).

Special feature
- You can click the cat icon to change the system prompt.
- You can use the slider to change the temperature/Top-P/presence penalty (larger values will make the model more creative, but also more likely to generate nonsense).
- You can click the Render/Source button to switch between the rendered and source code of the page.



