# 📘 MCP Wikipedia Summary Client & Server

This project implements a lightweight **Model Context Protocol (MCP)** client and server that work together to provide fast, structured access to **Wikipedia article summaries**.  
It allows any MCP-compatible AI model or toolchain to request a topic and receive a clean, concise summary pulled directly from Wikipedia.
**This project is also a reusable template for developing and testing custom MCP clients and servers locally, accelerating future MCP-based tool development.
**---

## 🚀 Features

- **MCP server** that exposes a `wikipedia_summary` tool  
- **MCP client** that communicates with the server using the MCP protocol  
- Retrieves **real-time Wikipedia summaries** for any given topic  

---

## ▶️ How to Run This MCP Project

### **Step 1 — Clone the Repository**

### **Step 2 — Set Up Ollama**

Install **Ollama Desktop**

Install the **gemma3:1b** model:
```bash
ollama pull gemma3:1b
```
### **Step 3 — Set Up the Python Virtual Environment**

Create a virtual environment:
```bash
python -m venv venv
```
Activate the virtual environment (PowerShell):
```bash
venv\Scripts\Activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```
### **Step 4 — Run the MCP Client**
```bash
python mcp_client.py
```
