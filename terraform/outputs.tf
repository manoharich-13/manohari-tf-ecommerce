output "api_base_url" {
  value = aws_api_gateway_stage.dev.invoke_url
}

output "products_url" {
  value = "${aws_api_gateway_stage.dev.invoke_url}/products"
}

output "cart_url" {
  value = "${aws_api_gateway_stage.dev.invoke_url}/cart"
}

output "pay_url" {
  value = "${aws_api_gateway_stage.dev.invoke_url}/pay"
}

output "auth_register_url" {
  value = "${aws_api_gateway_stage.dev.invoke_url}/auth/register"
}

output "auth_login_url" {
  value = "${aws_api_gateway_stage.dev.invoke_url}/auth/login"
}

