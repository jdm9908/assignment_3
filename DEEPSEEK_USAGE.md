# How I Used DeepSeek

## What I Did

I used DeepSeek AI to analyze power plant capacity factors and flag the weird ones. Instead of just using basic rules I wanted something that understood different fuel types have different normal ranges.

## The Prompt I Used

I sent this exact prompt to DeepSeek for each batch of plants:

Analyze the following power plant capacity factors and flag any unusual patterns. Consider fuel type typical ranges and seasonal factors this is February 2025 data.

For each plant return a flag category:
Normal Expected performance for fuel type
High_[FuelType] Above typical range but reasonable  
Low_[FuelType] Below typical range
Extreme_[FuelType] Significantly outside normal bounds
Mixed_Fuel_Unusual Complex multi-fuel scenarios

Plant data:
[JSON array with plantName fuelType capacityFactor capacity state]

Return only a JSON object mapping plant names to flag categories.

## Why This Worked

I told it the timeframe so it knows February means low solar. I gave it clear categories to use. I asked for JSON so I could parse it easily. The fuel type awareness was key because nuclear at 80% is different than solar at 80%.

## How I Processed Everything

I sent 25 plants per request with 2 second delays between batches. This took 46 batches total for 1145 plants. I got 100% success with no rate limit problems.

If a batch failed I had backup logic to use basic rules instead. I filtered out plants with missing data first. Each request included plant name fuel type capacity factor total capacity and state.

## What Worked Best

The AI was really good at fuel specific analysis. It knew nuclear plants typically run 80-100% and anything over 105% is high. Solar plants in February should be 15-25% so 30% would be high. Wind can be 25-45% normally and 60%+ is high performance.

It also understood seasonal patterns. February means lower solar output and higher heating demand for gas plants. The AI handled multi-fuel plants by looking at the combined performance against mixed expectations.

## Problems I Had

DeepSeek has rate limits so I added 2 second delays and that fixed it. Plant names sometimes came back in different formats but exact matching with error handling worked. The AI responses sometimes had extra text around the JSON so I wrote code to extract just the JSON part. EIA uses inconsistent fuel naming but the AI handled that naturally.

## Results I Got

Most plants got flagged as AI_Normal which makes sense. 208 plants got AI_Low_Solar which is expected in February. 102 plants got AI_High_Wind showing good winter performance. The nuclear plants that got flagged high were actually performing well not broken.

## Interesting Things I Found

I could see regional patterns when I combined the flags with state data. Texas wind farms showed high winter performance. Florida solar was appropriately low for February. Nuclear plants in the Southeast were consistently high performers.

You can use the flags to benchmark utilities. Plants with same fuel but different flags show operational differences. Extreme flags might indicate equipment problems or exceptional efficiency.

## Cost and Time

Processing 1145 plants in 46 batches took about 2 minutes total. DeepSeek pricing is cheap so cost was minimal. The value is way higher than basic rule systems because it actually understands context.