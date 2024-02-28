FROM elixir:1.16.1

# Install inotify-tools for file watching
RUN apt-get update && apt-get install -y inotify-tools

# Set up working directory
WORKDIR /app

# Run dependencies
COPY mix.exs mix.lock ./
RUN mix deps.get

# Copy the rest of the application
COPY . .

RUN mix ecto.setup

# Export port 4000
EXPOSE 4000

# Start Phoenix endpoint
CMD ["mix", "phx.server"]
