# Virtual Lenny
>  Retrieval-Augmented Generation (RAG) system that recreates **Lenny Rachitsky’s product thinking style** using AWS serverless infrastructure, vector search, and real-time WebSocket streaming.

This project builds a **full end-to-end RAG pipeline**  from scraping real PM content to serving low-latency, streaming answers in a  web UI.

**Target persona**:  [Lenny Rachitsky on LinkedIn](https://www.linkedin.com/in/lennyrachitsky/)


---

## Demo
![Virtual Lenny Demo](./results/virtual-lenny-demo.gif)

**Live demo**:  
🌐 https://virutal-lenny-with-eval.vercel.app/


> NOTE : The first response might take around **7 -12** seconds because I’m using a **mxbai-embed-large-v1** for better retrieval quality (see ablation results below). Loading it adds some latency, but the quality boost was worth it for now. Optimizing this tradeoff is an active direction I plan to explore.



---

## 📌 Why This Project Exists

- Explore **production-ready RAG architecture**
- Learn **AWS Step Functions + WebSocket APIs**
- Build a **persona-aware assistant** grounded in real content
- Understand real-world infra issues (timeouts, embeddings, Docker, Next.js, Qdrant)

This project was built as part of a **Vectorial / MLOps-style system design assignment**, but evolved into a full stack, deployable system.

---

## 🧠 High-Level Architecture


What surprised Matt MacInnis about his transition from COO to CPO at Rippling?


What's Lovable's key strategy for growth according to Elena Verna?

What are some key insights Fei-Fei Li shares about the development and future of AI?


When might it be wise to consider quitting a startup project according to Matt MacInnis?



Alright yes , sounds good ! Good night :)