defmodule TutorApp.Repo.Migrations.CreateChatbotConversations do
  use Ecto.Migration

  def change do
    create table(:chatbot_conversations) do

      timestamps(type: :utc_datetime)
    end
  end
end
