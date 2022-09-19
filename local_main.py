"""
@Authors: A’Qilah Ahmad Dahalan, Jaime Aparicio Estrems, Benjamin Baffy, Sumit Gore, Matteo Mastroguiseppe
@Date: 2022.09.19
@Links: https://github.com/Hawe-e1/HAWE_Feature_Based_Assembly_Process
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("procgen.api:app", port=8000, log_level="info", reload=True)
