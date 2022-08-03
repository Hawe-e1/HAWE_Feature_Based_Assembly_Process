FROM conda/miniconda3

RUN conda install -c conda-forge python=3.10 sympy fastapi uvicorn 

COPY ./procgen /assembly-steps-gen/procgen
COPY start.sh /assembly-steps-gen/start.sh

WORKDIR /assembly-steps-gen

RUN chmod +x /assembly-steps-gen/start.sh

CMD ["./start.sh"]
