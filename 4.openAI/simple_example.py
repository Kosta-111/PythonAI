from openai import OpenAI

client = OpenAI(api_key="my-api-key-here")

response = client.responses.create(
    model="gpt-4.1",
    input="Як завести кота?. Покроковий алгоритм."
)

print(response.output_text)