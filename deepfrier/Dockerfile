FROM node:lts-alpine3.12
WORKDIR /home/node/app
COPY ./ ./

RUN apk add imagemagick
RUN npm install
#USER node
CMD ["node", "app.js"]
