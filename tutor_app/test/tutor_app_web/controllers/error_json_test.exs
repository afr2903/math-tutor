defmodule TutorAppWeb.ErrorJSONTest do
  use TutorAppWeb.ConnCase, async: true

  test "renders 404" do
    assert TutorAppWeb.ErrorJSON.render("404.json", %{}) == %{errors: %{detail: "Not Found"}}
  end

  test "renders 500" do
    assert TutorAppWeb.ErrorJSON.render("500.json", %{}) ==
             %{errors: %{detail: "Internal Server Error"}}
  end
end
