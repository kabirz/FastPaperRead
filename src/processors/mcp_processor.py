from fastmcp import Client
import re
import os


# 获取关键词
async def get_keywords(tex_content: str):
    url = os.environ.get('SERVER_GET_KEYWORD')
    keyworks = ''
    async with Client(url) as mcp_client:
        tools = await mcp_client.list_tools()
        result = await mcp_client.call_tool(tools[0].name, {"question": tex_content})
        for content in result.content:
            keyworks += content.text

    keyworks = keyworks.replace('\n', ' ')
    keyworks = re.sub(r" +", " ", keyworks)
    keyworks = keyworks.replace('、', ' ')
    return keyworks
    
# 获取论文相关链接
async def get_link(keywords: str):
    url = os.environ.get('SERVER_SEARCH_LINK')
    async with Client(url) as mcp_client:
       tools = await mcp_client.list_tools()
       result = await mcp_client.call_tool(tools[0].name, {"question": keywords})
       url_list = []
       for content in result.content:
           for line in content.text.split('\n'):
               if 'link' in line.lower():
                   matches = re.findall(r'.*"link":\s*"(https?://[^\s"]+)".*', line)
                   if matches:
                       url_list.append(matches[0])
       return url_list

# 获取论文摘要
async def get_summary(tex_content: str):
    url = os.environ.get('SERVER_SUMMARY')
    message = ''
    async with Client(url) as mcp_client:
        tools = await mcp_client.list_tools()
        result = await mcp_client.call_tool(tools[0].name, {"question": tex_content})
        for content in result.content:
            message += content.text
    return message

#  获取论文相关知识
async def get_knowedge(tex_content: str, knowledges):
    url = os.environ.get('SERVER_KNOWLEDGE')
    message = ''
    async with Client(url) as mcp_client:
        tools = await mcp_client.list_tools()
        result = await mcp_client.call_tool(tools[0].name, {
            "question": tex_content,
            "mBlAVtk7": knowledges})
        for content in result.content:
            message += content.text
        if len(message) > 2:
            if message[0] == '[':
                message = message[1:]
            if message[-1] == ']':
                message = message[:-1]
    return message

#  生成博客
async def get_blog(tex_content: str, code_content, knowledges):
    url = os.environ.get('SERVER_GEN_BLOG')
    message = ''
    async with Client(url) as mcp_client:
        tools = await mcp_client.list_tools()
        result = await mcp_client.call_tool(tools[0].name, {
            'question':'开始',
            'tKEUT9iQ': tex_content,
            'gKxpZiRI': code_content,
            'ocN5KV4O': knowledges})
        for content in result.content:
            message += content.text
        if len(message) > 2:
            if message[0] == '[':
                message = message[1:]
            if message[-1] == ']':
                message = message[:-1]
    return message


