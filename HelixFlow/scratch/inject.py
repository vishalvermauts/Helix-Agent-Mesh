import time
import subprocess
import random

for i in range(15):
    model = random.choice(['deepseek-chat', 'gemini-1.5-pro', 'claude-3-5-sonnet-20240620'])
    provider = 'DeepSeek' if 'deepseek' in model else 'Google Gemini' if 'gemini' in model else 'Anthropic'
    cost = random.randint(10, 50)
    ttft = random.randint(30, 200)
    lat = ttft + random.randint(10, 100)
    cmd = f"ssh -i HelixFlow -o StrictHostKeyChecking=no root@165.227.185.117 \"redis-cli XADD gateway:telemetry * requested_model auto assigned_model {model} provider '{provider}' tenant_id test_user project project-alpha tags env:production masked_token 'sk-...1234' total_duration_ms {lat} time_to_first_token_ms {ttft} prompt_tokens 15 completion_tokens 50 tokens 65 initiated_epoch {time.time()}\""
    subprocess.run(cmd, shell=True)
    time.sleep(0.1)
