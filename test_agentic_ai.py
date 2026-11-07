from modules.llm_agent import run_llm_agent

print("\n======================================")
print("       SUPPLYCHAINIQ LLM AGENT")
print("======================================")

query = input("\nAsk SupplyChainIQ: ")

try:
    result = run_llm_agent(query)

    print("\n========== AI RESPONSE ==========")
    print(result["answer"])

    print("\n========== AGENT TOOL ACTIVITY ==========")

    for item in result["activity"]:
        print("\nTool:", item["tool"])
        print("Arguments:", item["arguments"])
        print("Result:", item["result"])

    print("\nTotal Tool Calls:", result["tool_calls"])

except Exception as error:
    print("\nAGENT ERROR:", error)