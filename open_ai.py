import os
import openai 

openai.api_key = "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"

def get_ai_answer(instruction, user_message):
  messages=[
    {"role": "system", "content": instruction},
    {"role": "user", "content": f"{user_message}"}
  ]
  completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=messages
  ) 
  answer = completion.choices[0].message.content
  # messages.append({"role": "assistant", "content": answer})
  # print(messages)
  return answer



def get_response_to_request(character, msg_from_user):
    if character=="rick":
        instruction = "You are Rick - fictional character from the American animated television series 'Rick and Morty'. Do not give dangerous information"
    if character=='harry':
        instruction = "You are Harry Potter -  fictional character from a series of fantasy novels written by British author JK Rowling.'. Do not give dangerous information"
    response = get_ai_answer(instruction=instruction, user_message=msg_from_user)
    return response