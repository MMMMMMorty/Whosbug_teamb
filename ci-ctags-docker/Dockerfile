FROM python:3.8.2-alpine3.11 
ADD AddSupportLanguage/*.ctags /root/.ctags.d/
ADD TestingFiles /root/TestingFiles
ADD ctags /root/ctags
ADD *.py /root/

RUN \
  # add runtime dependencies
  apk --update --no-cache add jansson yaml libxml2 && \
  # add build dependencies
  apk --update --no-cache add --virtual build-deps \
    git autoconf make gcc automake musl-dev \
    jansson-dev yaml-dev libxml2-dev && \
  apk --update --no-cache add bash && \
  # add requests
  pip install requests && \
  # build, install universal-ctags
  cd ~/ctags && \
  ./autogen.sh && \
  ./configure --program-prefix=u && \
  make && make install && \
  # cleanup
  cd ~ && rm -rf ctags && \
  apk del build-deps
WORKDIR /root
CMD ["python"]
