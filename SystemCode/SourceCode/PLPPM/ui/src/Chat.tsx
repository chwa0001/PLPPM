import { Box } from '@mui/material';
import dayjs from 'dayjs';
import React from 'react';

import { ChatController } from './chat-controller';
import {
  ActionRequest,
  CustomActionRequest,
  MultiSelectActionRequest,
  SelectActionRequest,
  TextActionRequest,
} from './chat-types';

import { ChatMessage } from './ChatMessage';
import { MultiSelectInput } from './MultiSelectInput';
import { SelectInput } from './SelectInput';
import { TextInput } from './TextInput';

export function Chat({
  chatController,
}: React.PropsWithChildren<{
  chatController: ChatController;
}>): React.ReactElement {
  const chatCtl = chatController;
  const [messages, setMessages] = React.useState(chatCtl.getMessages());
  const [actReq, setActReq] = React.useState(chatCtl.getActionRequest());

  const msgRef = React.useRef<HTMLDivElement>(null);
  const scroll = React.useCallback((): void => {
    if (msgRef.current) {
      msgRef.current.scrollTop = msgRef.current.scrollHeight;
      // msgRef.current.scrollIntoView(true);
    }
  }, [msgRef]);
  React.useEffect(() => {
    function handleMassagesChanged(): void {
      setMessages([...chatCtl.getMessages()]);
      scroll();
    }
    function handleActionChanged(): void {
      setActReq(chatCtl.getActionRequest());
      scroll();
    }
    chatCtl.addOnMessagesChanged(handleMassagesChanged);
    chatCtl.addOnActionChanged(handleActionChanged);
  }, [chatCtl, scroll]);

  type CustomComponentType = React.FC<{
    chatController: ChatController;
    actionRequest: ActionRequest;
  }>;
  const CustomComponent = React.useMemo((): CustomComponentType => {
    if (!actReq || actReq.type !== 'custom') {
      return null as unknown as CustomComponentType;
    }
    return (actReq as CustomActionRequest)
      .Component as unknown as CustomComponentType;
  }, [actReq]);

  const unknownMsg = {
    type: 'text',
    content: 'Unknown message.',
    self: false,
  };

  let prevDate = dayjs(0);
  let prevTime = dayjs(0);

  return (
    <Box
      sx={{
        height: '100%',
        width: '100%',
        p: 1,
        bgcolor: 'background.default',
        display: 'flex',
        flexDirection: 'column',
        '& > *': {
          maxWidth: '100%',
          minHeight:'80vh',
        },
        '& > * + *': {
          mt: 1,
          minHeight:'5vh',
        },
      }}
    >
      <Box
        sx={{
          flex: '1 1 80%',
          overflowY: 'auto',
          WebkitOverflowScrolling: 'touch',
          display: 'flex',
          flexDirection: 'column',
          '& > *': {
            maxWidth: '100%',
          },
        }}
        ref={msgRef}
      >
        {messages.map((msg): React.ReactElement => {
          let showDate = false;
          let showTime = !!chatCtl.getOption().showDateTime;
          
          if (!!chatCtl.getOption().showDateTime && !msg.deletedAt) {
            const current = dayjs(
              msg.updatedAt ? msg.updatedAt : msg.createdAt,
            );

            if (current.format('YYYYMMDD') !== prevDate.format('YYYYMMDD')) {
              showDate = true;
            }
            prevDate = current;

            if (current.diff(prevTime) < 50) {
              showTime = false;
            } else {
              prevTime = current;
            }
          }
          if (msg.type === 'text' || msg.type === 'jsx') {
            return (
              <ChatMessage
                key={messages.indexOf(msg)}
                id={`cu-msg-${messages.indexOf(msg) + 1}`}
                message={msg}
                showDate={true}
                showTime={true}
              />
            );
          }
          return (
            <ChatMessage
              key={messages.indexOf(msg)}
              id={`cu-msg-${messages.indexOf(msg) + 1}`}
              message={unknownMsg}
              showDate={true}
              showTime={true}
            />
          );
        })}
      </Box>
      <Box
        sx={{
          flex: '0 1 auto',
          display: 'flex',
          alignContent: 'flex-end',
          '& > *': {
            minWidth: 0,
          },
        }}
      >
        {actReq && actReq.type === 'text' && (
          <TextInput
            chatController={chatCtl}
            actionRequest={actReq as TextActionRequest}
          />
        )}
        {actReq && actReq.type === 'select' && (
          <SelectInput
            chatController={chatCtl}
            actionRequest={actReq as SelectActionRequest}
          />
        )}
        {actReq && actReq.type === 'multi-select' && (
          <MultiSelectInput
            chatController={chatCtl}
            actionRequest={actReq as MultiSelectActionRequest}
          />
        )}
        {actReq && actReq.type === 'custom' && (
          <CustomComponent
            chatController={chatCtl}
            actionRequest={actReq as CustomActionRequest}
          />
        )}
      </Box>
    </Box>
  );
}