# 🧬 Helix Engine & Helix Flow: Distributed High-Availability Agent Mesh

**Video Demo Link:** [Insert YouTube URL Here]

## 🚀 The Pitch (Track: Reasoning Agents)

**The Problem:** 
Enterprise teams struggle to deploy autonomous agent swarms in production because they lack resilient infrastructure. Routing all requests to premium models (like GPT-4o) incurs massive costs and latency. Furthermore, passing untrusted inputs to autonomous agents poses severe security and compliance risks.

**The Solution:**
We built the **Helix High-Availability Agent Mesh**, a production-grade orchestration and routing framework designed specifically for the Microsoft Hackathon's Reasoning Agents track. 

Helix separates the architecture into a heavily decoupled 4-Tier topology:
1. **Helix Flow Gateway (Tier 1 Ingress):** An ultra-low latency routing proxy that calculates intent via closed-form NumPy matrices in under 15ms.
2. **Helix Engine (Tier 2 Swarm Core):** The master orchestrator managing complex code workspaces and tree-sitter logic.
3. **Edge Compute Node (Tier 3):** A dedicated edge node running local Qwen 3.6 Coder models for zero-cost execution of simple tasks.
4. **Diagnostic Lab (Tier 4):** An out-of-band evaluation harness for 5-iteration benchmarking tests.

## 🧠 Microsoft Ecosystem Integration

We went all-in on the Microsoft AI stack to ensure enterprise-grade safety, observability, and reasoning:

* **Azure AI Foundry Catalog:** We completely replaced standard public endpoints. The Helix Flow Gateway now routes dynamically using circuit breakers pointing to the Azure AI Foundry Catalog (`gpt-4o`).
* **Azure AI Content Safety:** We built an asynchronous middleware interceptor (`AzureContentSafetyInterceptor`) that scans all incoming prompts for prompt injections or toxic inputs before they ever reach the routing matrix.
* **Microsoft IQ Grounding:** Inside the Helix Engine's episodic memory, we engineered a `FoundryIQGrounding` class. Before generating code, the agent dynamically fetches strict mock enterprise constraints (e.g., Azure SQL ACID compliance) and injects them directly into the agent's context window.
* **Azure Application Insights (OpenTelemetry):** We instrumented the hot routing path inside `dispatch_matrix.py` with OpenTelemetry. Span attributes (tokens, selected fabric, latency) are emitted out-of-band directly to Azure Application Insights to prove our sub-15ms overhead without slowing down the proxy.

## 🛠️ Why It Fits the Reasoning Agents Track
Helix isn't just an agent script—it's the **enterprise nervous system** required to run agents safely. By leveraging Azure AI Foundry for inference, Azure AI Content Safety for defense, Application Insights for observability, and our custom Microsoft IQ Grounding memory systems, we've demonstrated how to take autonomous multi-agent reasoning from a local sandbox to a highly resilient, cost-effective production deployment.

*(Note: Telemetry data, tokens spent, and profiles shown in our demo logs are Synthetic Evaluation Logs used for demonstration compliance).*

## 📐 High-Availability Architecture Diagram

```mermaid
graph TD
    %% Tiers
    subgraph Tier 1: Ingress Layer
        A[Droplet 1: Helix Flow Gateway]
    end

    subgraph Tier 2: Swarm Core
        B[Droplet 2: Helix Engine Master]
    end

    subgraph Tier 3: Edge Compute
        C[Droplet 3: Local Ollama Node]
    end

    subgraph Microsoft Cloud
        D[Azure AI Foundry: gpt-4o]
        E[Azure App Insights: Telemetry]
        F[Azure AI Content Safety]
    end

    %% Flow
    User((User)) -->|HTTPS Prompt| A
    A -->|Async Interceptor| F
    F -->|Safe Payload| A
    A -.->|OpenTelemetry Metrics| E
    
    A -->|Complex Intent <br> 15ms routing| D
    A -->|Simple Intent <br> Fallback| C
    
    D --> B
    C --> B
    B -->|Foundry IQ Grounding| D
```
