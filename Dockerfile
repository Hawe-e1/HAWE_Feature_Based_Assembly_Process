FROM conda/miniconda3

RUN conda install -c conda-forge python=3.10 sympy fastapi uvicorn 

COPY ./procgen /assembly-steps-gen/procgen
COPY main.py /assembly-steps-gen/main.py

WORKDIR /assembly-steps-gen

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["./start.sh"]
