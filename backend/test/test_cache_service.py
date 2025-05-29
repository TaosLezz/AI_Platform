import time
from services.cache_service import cache_service

def test_cache():
    service_type = "chat"
    input_data = {"prompt": "Hello, how are you?"}
    parameters = {"language": "en"}
    result = {"response": "I'm fine, thank you!"}

    print("▶ Checking Redis availability...")
    if not cache_service.is_available:
        print("❌ Redis is not available")
        return

    print("▶ Setting cache...")
    success = cache_service.set(service_type, input_data, result, parameters)
    print("✅ Set cache:", success)

    print("▶ Getting cache...")
    cached = cache_service.get(service_type, input_data, parameters)
    print("✅ Cached result:", cached)

    print("▶ Cache stats:")
    stats = cache_service.get_cache_stats()
    print(stats)

    print("▶ Reset stats...")
    cache_service.reset_stats()

    print("▶ Cache after reset:")
    print(cache_service.get_cache_stats())

if __name__ == "__main__":
    test_cache()
