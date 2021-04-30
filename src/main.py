from fastapi import FastAPI


app = FastAPI()


@app.get("/test")
async def test():
    return {
        "result": "success",
        "message": "It works!",
    }
