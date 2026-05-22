resource "aws_sns_topic" "billing_alerts" {
  provider = aws.us_east_1
  name     = "${var.project_name}-billing-alerts"
}

resource "aws_sns_topic_subscription" "billing_alerts_email" {
  provider  = aws.us_east_1
  count     = var.billing_alarm_email == null ? 0 : 1
  topic_arn = aws_sns_topic.billing_alerts.arn
  protocol  = "email"
  endpoint  = var.billing_alarm_email
}

resource "aws_cloudwatch_metric_alarm" "billing_alarm" {
  provider            = aws.us_east_1
  alarm_name          = "${var.project_name}-monthly-billing-alarm"
  alarm_description   = "Triggers when estimated AWS charges reach the configured monthly threshold."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  threshold           = var.billing_alarm_threshold
  period              = 21600
  statistic           = "Maximum"
  namespace           = "AWS/Billing"
  metric_name         = "EstimatedCharges"
  dimensions = {
    Currency = "USD"
  }
  alarm_actions = [aws_sns_topic.billing_alerts.arn]
}