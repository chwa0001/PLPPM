import { useState, useMemo } from 'react'
import { Box, Divider, Typography } from '@mui/material'
import './App.css'
import {Chat} from './Chat'
import { ChatController } from './chat-controller';

async function echo({chatCtl,conversation,previousReply,previousRequest}
  :{chatCtl: ChatController,conversation:number,previousReply?:string,previousRequest?:string})
  : Promise<void> {
  var intention;
  if(previousRequest && !previousReply){
    await chatCtl.addMessage({
      type: 'text',
      content: `What is the database you want to query?`,
      self: false,
      avatar: '/static/bot.png',
      createdAt:new Date(),
    });
    const intent = await chatCtl.setActionRequest({
      type: 'select',
      options: [
        {
          value: 'sql',
          text: 'Statistical Performance Indicators (SPI) dataset by The World Bank',
        },
        {
          value: 'gql',
          text: 'US Financial News Articles',
        },
        {
          value: 'terms',
          text: 'Investopedia Finanical Terms',
        },
        {
          value: 'casual',
          text: 'Casual talk with bot',
        },
        {
          value: 'exit',
          text: 'Exit',
        },
      ],
    });
    intention = intent.select;
  };

  const text = !intention?await chatCtl.setActionRequest({
      type: 'text',
      placeholder: 'Please enter something',
  }):{value:intention};
  
  if(text.value.trim() && intention!=='exit'){
    const abortSignal = new AbortController();
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal:abortSignal.signal,
      body: JSON.stringify({
        data:{
          text:text.value,
          conversation:conversation,
          in_response_to:previousReply,
          previous_request:previousRequest,
          intent:intention,
        }
      }),
  };
  await fetch('/chat',requestOptions)
  .then(function(response){
    if(!response.ok){
      return response.json().then(text => {throw new Error(text['Bad Request'])})
    }
    else{
      return response.json()
    }
  }).then(
    (data) => {
      if(data.tags.includes('sql')){
        chatCtl.addMessage({
          type: 'text',
          content: `Generated SQL query: ${data.sql_query}`,
          self: false,
          avatar: '/static/bot.png',
          createdAt: data.created_at,
        });
      }
      else if(data.tags.includes('gql')){
        chatCtl.addMessage({
          type: 'text',
          content: `Generated GQL query: ${data.gql_query}`,
          self: false,
          avatar: '/static/bot.png',
          createdAt: data.created_at,
        });
      }
      chatCtl.addMessage({
        type: 'text',
        content: `${data.text}`,
        self: false,
        avatar: '/static/bot.png',
        createdAt: data.created_at,
      });
      echo({chatCtl:chatCtl,conversation:conversation,previousReply:data.text,previousRequest:text.value});
    },(error) => {
      console.log(error);
      echo({chatCtl:chatCtl,conversation:conversation,previousRequest:text.value});
    }
  )
  }
  else{
    if (intention==='exit'){
      const queryText = `How may I help you?`
      chatCtl.addMessage({
        type: 'text',
        content: queryText,
        self: false,
        avatar: '/static/bot.png',
        createdAt: new Date(),
      });
      echo({chatCtl:chatCtl,conversation:conversation,previousReply:queryText,previousRequest:previousRequest});
    }
    else{
      console.log(previousRequest);
      echo({chatCtl:chatCtl,conversation:conversation,previousRequest:previousRequest});
    }
    
  }
}


function App() {
  const [chatCtl] = useState(new ChatController({showDateTime: true,}),);
  const [conversationID, setConversationID] = useState(0);
  useMemo(() => {
    setConversationID((value)=>{
      return value + 1
    });
    const greetingText = `Hello I am a bot. How may I help you?`
    chatCtl.addMessage({
      type: 'text',
      content: greetingText,
      self: false,
      avatar: '/static/bot.png',
      createdAt:new Date(),
    });
    echo({chatCtl:chatCtl,conversation:conversationID,previousReply:greetingText});
  }, [chatCtl]);

  return (
      <Box flexDirection='column'>
      <Box>
      <Typography>
      Conversational natural language query of relational and non-relational databases
      </Typography>
      </Box>
      <Divider/>
      <Chat chatController={chatCtl}/>
      </Box>
  )
}

export default App
