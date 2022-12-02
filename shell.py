import BananaLang

while True:
    text = input("BananaLang> ")
    result, error = BananaLang.run("<console>", text)

    if error: print(error.as_string())
    elif result: print(result)