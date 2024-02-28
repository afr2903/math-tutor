defmodule TutorApp.Repo do
  use Ecto.Repo,
    otp_app: :tutor_app,
    adapter: Ecto.Adapters.Postgres
end
