
# Automation

Basically just a script to automatically label my emails and move them out of inbox

**NOT** actually recommended to use since I haven't extracted a template for associating emails
with labels, so running `process` will label per my requirements and probably fail

## Credentials

`GOOGLE_API_TOKEN`

## Usage

```
# Install dependencies
pip install -r requirements.txt

# Update list of labels
python main.py label

# Process emails using list of labels and inbuilt regex selectors
python main.py process
```
