ad_filter_template3 = """
Given a document, analyze and determine whether it can be classified as advertisement.
Here are some key factors to consider:
- Purpose and Tone: Advertisements often aim to promote a product, service, or brand. The language may be persuasive and enthusiastic, using words that invoke emotion or urgency, like "Buy now!" or "Limited time offer!"
- Contact Information: Look for contact details for a business or organization. Advertisements often include phone numbers, addresses, websites, or QR codes to direct potential customers.
- Offers and Promotions: Discounts, special offers, and promotions are common in advertisements.
- Language and Style: Advertisements may use exaggerated or superlative language, such as "the best," "the greatest," or "unbeatable." The writing style may lack depth or information, focusing more on persuasion rather than informing.
- Product or Service Description: Advertisements will often center around detailed descriptions of a product or service, emphasizing its benefits and advantages.
- Regulatory Information: Some jurisdictions require specific labeling or disclaimers for advertisements. Look for phrases like "Sponsored content," "Advertisement," or something similar.
- Platform or Context: Consider where you found the document. Was it in a magazine filled with other advertisements? On a website known for advertising? Context can provide valuable clues.
- Links to Purchase: Advertisements often contain direct links or instructions to purchase the product or service.
- Check for Bias: Advertisements may contain biased information, presenting only the positive aspects of a product or service without discussing any drawbacks or competing alternatives.

Based on the above factors, provide a score scale (1-10), with 1 being "non-advertisement", 10 being advertisement. You can only provide the score and do not output other things. 

{}
"""
