FROM eclipse-temurin:25-jdk-alpine AS build
WORKDIR /build
COPY backend-java/FoodGateway.java .
RUN javac FoodGateway.java

FROM eclipse-temurin:25-jre-alpine
WORKDIR /app
COPY --from=build /build/FoodGateway.class .
COPY frontend ./frontend
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=70"
EXPOSE 8080
CMD ["java", "FoodGateway", "/app/frontend"]
