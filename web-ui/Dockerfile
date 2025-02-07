FROM node:20.11.0 AS build

WORKDIR /web-ui
COPY package.json package-lock.json ./
RUN npm i
COPY . ./

ARG API_URL
ENV VITE_API_URL=$API_URL

RUN npx quasar build

FROM nginx:alpine
COPY --from=build /web-ui/dist/spa /web-ui-statics
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
