defmodule TutorApp.Chatbot.Message do
  use Ecto.Schema
  import Ecto.Changeset

  schema "chatbot_messages" do
    field :content, :string
    field :role, :string

    belongs_to :conversation, TutorApp.Chatbot.Conversation

    timestamps()
  end

  @doc false
  def changeset(message, attrs) do
    message
    |> cast(attrs, [:role, :content])
    |> validate_required([:content])
  end
end
