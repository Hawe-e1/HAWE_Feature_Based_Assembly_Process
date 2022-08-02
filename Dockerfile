FROM conda/miniconda3

RUN conda install -c conda-forge python=3.10 sympy fastapi uvicorn 

COPY ./procgen /assembly-steps-gen/procgen

WORKDIR /assembly-steps-gen

RUN uvicorn procgen.api:app --reload 
