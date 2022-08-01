FROM conda/miniconda3

RUN conda install python=3.10 sympy fastapi uvicorn 

RUN uvicorn procgen.api:app --reload 
