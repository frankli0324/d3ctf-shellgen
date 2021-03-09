ARG flag=d3ctf{flag_here}

FROM gcc AS builder
ARG flag

COPY getflag.cpp getflag.cpp
COPY sleep.cpp sleep.cpp
RUN sed -i "s/flag_here/$flag/g" getflag.cpp
RUN g++ getflag.cpp -o getflag -static
RUN g++ sleep.cpp -o sleep -static

FROM scratch
COPY --from=builder getflag /getflag
COPY --from=builder sleep /sleep
CMD ["/sleep"]
