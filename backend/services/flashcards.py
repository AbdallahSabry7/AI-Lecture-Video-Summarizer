from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import textwrap

model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate(text, max_len=256):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=max_len,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# 1. Split transcript into chunks
def chunk_text(text, chunk_size=900):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) 
            for i in range(0, len(words), chunk_size)]

# 2. Generate Q&A for each chunk
def generate_flashcards_from_chunk(chunk, num_questions=5):
    # Step A: generate questions from transcript chunk
    question_prompt = f"""
Generate {num_questions} important student questions based on the following lecture transcript:

TRANSCRIPT CHUNK:
{chunk}

Questions:
"""
    questions = generate(question_prompt)

    # Step B: generate answers
    flashcards = []
    for q in questions.split("\n"):
        if q.strip():
            answer_prompt = f"""
Answer the following question using the transcript below:

TRANSCRIPT:
{chunk}

QUESTION:
{q}

ANSWER:
"""
            answer = generate(answer_prompt)
            flashcards.append((q.strip(), answer.strip()))

    return flashcards

# ------------------------
# MAIN PIPELINE
# ------------------------
transcript = """
I  you  you  Thank you.  I'm really excited to share with you some finding  that really surprised me about what makes  companies succeed the most. What factors actually matter  the most for start-up success.  I believe that the startup organization is one of the greatest  to make the world a better place.  If you take a group of people with the right equity incentive  and organize them in a startup you can unlock human  potential in a way never before possible.  them to achieve unbelievable things.  But the startup organization is so great, why does so many fail?  That's what I wanted to find out. I wanted to find out what actually  matters most for start-up success.  to try to be systematic about it. Avoid all my instincts and  Maybe misperceptions I have from so many companies I've seen over the years.  I wanted to know this because I've been starting business  since I was 12 years old. When I sold candy at the bus stop.  in junior high school. To high school when I made solar energy  to college when I made loudspeakers.  I started software companies. And 20 years ago, I started  And at the last 20 years, we started more than a hundred percent.  many successes and many big failures.  We learned a lot from those failures.  look across what factors accounted the most.  for company success and failure. So I looked at these files.  I used to think that the idea was everything.  I mean, I name my company Idealab and how much I worship.  moment when you first come up with the idea. But then over time,  I came to think that maybe the team, the execution.  adaptability that mattered even more than the idea. I never  thought it be quoting boxer Mike Tyson on the test  But he once said, everybody,  Everybody has a plan until they get punched in the face.  And I think that's so true about business as well  So much about a team's execution.  is its ability to adapt to getting punched in the face by the  customer. The customer is the true reality. And that's why I became  I can't think that the team maybe was the most important thing  Then I started looking at the business model.  have a very clear path generating customer revenues.  started rising to the top in my thinking about maybe what mattered most  for success. I looked at the funding, sometimes companies  received intense amount of funding. Maybe that's the most important thing.  And then of course the timing is the idea way too early.  and the world's not ready for it? Is it early, meaning you're in advance?  and you have to educate the world, is it just right or is it too late?  too many competitors. So I tried to look very carefully at these  five factors across many companies. And I looked across  all 100 idealize companies and 100 non-idealize companies.  companies to try and come up with something scientific about it.  So first, on these idea lab companies,  The top five companies, city search, cars direct.  Go to net zero tickets.com. Those all became billion dollars.  successes. And the five companies on the bottom, z.com  insider pages, my life, desktop factory people link. We all have  high hopes for but didn't succeed. So I tried to  across all of those attributes, how I felt those  companies scored on each of those dimensions. And then for none,  I looked at wild successes like air  Airbnb, Instagram, and Uber, and YouTube, been linked in.  and some failures. Web then, CosmoPets.com.  lose in Friendster. The bottom company's had intense fun  They even had business models in some cases, but they didn't succeed.  I tried to look at what factors actually counted the most for success.  and failure across all these companies. And the results really  surprised me. The number one thing was timing.  Timing accounted for 42%.  of the difference between success and failure.  execution came in second and the idea, the different  The idea of the unique idea that actually came in third.  Now this isn't absolutely definitive, it's not to say that the idea isn't important.  But it very much surprised me that the idea wasn't the most important.  most important thing. Sometimes it mattered more when it was actually time.  The last two business model in funding made sense to  to me actually. I think business model makes sense to be that low because  You can start out without a business model and then add one later if your customers are to make  and what you're creating. And funding, I think as well.  If you're underfunded at first, but you're gaining traction, it's  especially in today's age, it's very, very easy to get intense  So now let me give you some specific examples about  So take a while success like Airbnb.  everybody knows about. Well, that company was famously passed on by many  smart investors because people thought no one's going to rent  out a space in their home to a stranger. Of course, people  that wrong. But one of the reasons it succeeded aside from a good bit  a good idea, great execution is the  that company came out right during the height of the race.  recession when people really needed extra money.  help people overcome their objection to renting out their own home to a shrinkage.  same thing with Uber. Uber came out incredible  company, incredible business model, great execution too, but the timing.  was so perfect for their need to get drivers in  the system. Drivers were looking for extra money. It was very, very important.  some of our early successes. City search came out with  people need web pages. Go to.com, which we announced actually  was when companies were looking for cost-effective ways to  to get traffic. We thought the idea was so great, but actually the timing was  probably made me more important. And then some of our failures.  We started a company called z.com. It was an online entertainment company.  We were so excited about it. We raised enough money. We had a great business model  We need to sign incredibly great Hollywood talent to join  in the company. But broadband penetration was too low.  1999 2000 it was too hard to watch video content  content online, you had to put codecs in your browser and do all this stuff.  company eventually went out business in 2003. Just two years later.  later when the codec problem was solved by Adobe Flash.  And when broadband penetration crossed 50% of the  America, YouTube was perfectly time. Great idea.  but unbelievable timing. And in fact, YouTube didn't even have a business model.  when it first started. It wasn't even certain that that would work out.  but that was beautifully, beautifully timed. So what I was  say in summary is execution definitely matters.  matters a lot. The idea matters a lot. But timing might matter  even more. And the best way to really assess timing is to  really look, weather consumers are really ready for what you  to offer them and to be really, really honest about it, not me and deny it.  about any results that you see. Because if you have something you love, you want to put  But yet to be very, very honest about that factor on that.  timing. As I said earlier, I think start  to make the world a better place. I hope some of you will be able to see the world.  these insights can maybe help you have a slightly higher success  ratio and thus make something great come to the world.  that wouldn't have happened otherwise. Thank you very much for the great audience.  Thank you.  you"""

chunks = chunk_text(transcript, chunk_size=900)

all_flashcards = []

for i, chunk in enumerate(chunks, 1):
    print(f"\n--- Processing chunk {i}/{len(chunks)} ---\n")
    flashcards = generate_flashcards_from_chunk(chunk)
    all_flashcards.extend(flashcards)

# Display final flashcards
for i, (q, a) in enumerate(all_flashcards, 1):
    print(f"{i}. Q: {q}\n   A: {a}\n")
