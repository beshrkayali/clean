{
    "version": 2,
    "builds": [
        {
            "src": "clean.py",
            "use": "@now/python"
        }
    ],
    "routes": [
        {
            "src": "(.*)",
            "dest": "clean.py"
        }
    ]
}
