Simple "ask my documents" implementation in flask.

This work utilizes the llm setup by Scott W Harden documented here:
https://swharden.com/blog/2023-07-30-ai-document-qa/

Please note: the llm needs to be downloaded first.
This has been tested with the following two:

llama-2-7b-chat.ggmlv3.q8_0.bin (better accuracy, slower inference)
llama-2-7b-chat.ggmlv3.q4_1.bin (less accuracy, faster inference)

The pathes for the example above need to be indicated in the llm_evaluation.py as:
'./app/llm/llama-2-7b-chat.ggmlv3.q8_0.bin'
'./app/llm/llama-2-7b-chat.ggmlv3.q4_1.bin'