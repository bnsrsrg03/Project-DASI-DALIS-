FROM golang:1.22 AS b
WORKDIR /src
COPY . .
RUN go mod tidy && go build -o /server .
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=b /server /app/server
COPY model.json diare.db* /app/
CMD ["/app/server"]