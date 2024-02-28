defmodule TutorAppWeb.ChatbotLive.FormComponent do
  use TutorAppWeb, :live_component

  alias TutorApp.Chatbot

  @impl true
  def render(assigns) do
    ~H"""
    <div>
      <.form
        for={@form}
        id="message-form"
        phx-target={@myself}
        phx-change="change"
        phx-submit="save"
      >
        <.input field={@form[:content]} value={@content} type="text" placeholder="Type your message" />
      </.form>
    </div>
    """
  end

  @impl true
  def update(%{message: message} = assigns, socket) do
    changeset = Chatbot.change_message(message)

    {:ok,
     socket
     |> assign(assigns)
     |> assign(:content, "")
     |> assign_form(changeset)}
  end

  @impl true
  def handle_event("change", %{"message" => %{"content" => content}}, socket) do
    {:noreply, assign(socket, :content, content)}
  end

  @impl true
  def handle_event("save", %{"message" => message_params}, socket) do
    # Manually put user as role
    message_params = Map.put(message_params, "role", "user")

    case Chatbot.create_message(socket.assigns.conversation, message_params) do
      {:ok, message} ->
        notify_parent({:saved, message})
        {:noreply, assign(socket, :content, "")} # Reset input field after submit
      {:error, %Ecto.Changeset{} = changeset} ->
        {:noreply, assign_form(socket, changeset)}
    end
  end

  defp assign_form(socket, %Ecto.Changeset{} = changeset) do
    assign(socket, :form, to_form(changeset))
  end

  defp notify_parent(msg), do: send(self(), {__MODULE__, msg})
end
