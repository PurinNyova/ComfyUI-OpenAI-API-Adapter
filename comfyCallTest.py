# use this to test API
import openai 
client = openai.OpenAI(base_url="http://127.0.0.1:8001/v1", api_key="DidYouKnowThatVaporeon")  # No key needed
response = client.images.generate(
    model="hassaku-xl-illustrious-v22",
    prompt="A futuristic cityscape at sunset",
    n=1,
    size="1024x1024"
)
print(response.data[0].url)