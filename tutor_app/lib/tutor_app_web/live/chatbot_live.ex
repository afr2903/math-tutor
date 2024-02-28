defmodule TutorAppWeb.ChatbotLive do
  use Phoenix.LiveView, container: {:div, [class: "fixed right-0 bottom-0 mr-4"]}

  alias Phoenix.LiveView.JS

  alias TutorApp.Chatbot
  alias TutorApp.Chatbot.Message

  @impl true
  def mount(_params, _session, socket) do

    # For this tutorial, we are only working with a single conversation
    conversation =
      case Chatbot.list_chatbot_conversations() do
        [conversation|_] ->
          conversation
        _ ->
          {:ok, conversation} = Chatbot.create_conversation()
          conversation
      end

    {
      :ok,
      socket
      |> assign(:conversation, conversation)
      |> assign(:message, %Message{})
      |> assign(:messages, [])
    }
  end

  @impl true
  def handle_info({TutorAppWeb.ChatbotLive.FormComponent, {:saved, message}}, socket) do
    messages = [message|socket.assigns.messages]

    Task.async(fn ->
      Chatbot.generate_response(socket.assigns.conversation, messages)
    end)

    {
      :noreply,
      socket
      |> assign(:message, %Message{})
      |> assign(:messages, messages)
    }
  end

  def handle_info({ref, result}, socket) do
    Process.demonitor(ref, [:flush])

    messages =
      case result do
        {:ok, message} -> [message|socket.assigns.messages]
        _ -> socket.assigns.messages
      end

    {
      :noreply,
      socket
      |> assign(:messages, messages)
    }
  end

  @impl true
  def render(assigns) do
    ~H"""
    <div class="flex flex-col flex-grow w-full max-w-xl bg-white shadow-xl rounded-t-lg overflow-hidden">
      <div class="flex flex-col flex-grow p-4 overflow-auto max-h-[50vh]">
        <div class="flex w-full mt-2 space-x-3 max-w-xs">
          <img class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300" src="https://images.unsplash.com/photo-1589254065878-42c9da997008?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=2&amp;w=256&amp;h=256&amp;q=80" alt="">
          <div>
            <div class="bg-gray-300 p-3 rounded-r-lg rounded-bl-lg">
              <p class="text-sm">Hi. I am here to answer questions about Elixir.</p>
            </div>
            <span class="text-xs text-gray-500 leading-none">Now</span>
          </div>
        </div>
        <%= for message <- Enum.reverse(@messages) do %>
          <div id={"message-#{message.id}"} phx-mounted={JS.dispatch("scrollIntoView", to: "#message-#{message.id}")}>
            <div :if={message.role == "user"} class="flex w-full mt-2 space-x-3 max-w-xs ml-auto justify-end">
              <div>
                <div class="bg-blue-600 text-white p-3 rounded-l-lg rounded-br-lg">
                  <p class="text-sm"><%= message.content %></p>
                </div>
                <span class="text-xs text-gray-500 leading-none">Now</span>
              </div>
              <img class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300" src="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=2&amp;w=256&amp;h=256&amp;q=80" alt="">
            </div>

            <div :if={message.role == "assistant"} class="flex w-full mt-2 space-x-3 max-w-xs">
              <img class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300" src="https://images.unsplash.com/photo-1589254065878-42c9da997008?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=2&amp;w=256&amp;h=256&amp;q=80" alt="">
              <div>
                <div class="bg-gray-300 p-3 rounded-r-lg rounded-bl-lg">
                  <p class="text-sm"><%= message.content %></p>
                </div>
                <span class="text-xs text-gray-500 leading-none">Now</span>
              </div>
            </div>
          </div>
        <% end %>
      </div>

      <div class="bg-gray-300 p-4">
        <.live_component
          module={TutorAppWeb.ChatbotLive.FormComponent}
          id="new-message"
          conversation={@conversation}
          message={@message}
        />
      </div>
    </div>
    """
  end
end
