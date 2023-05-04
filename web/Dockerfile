FROM node:lts-alpine

WORKDIR /data/web
COPY package.json /data/web/package.json
# install project dependencies
RUN npm install

# Build environment
CMD ["npm", "run", "dev", "--host"]

# build app for production with minification
# RUN npm run build
