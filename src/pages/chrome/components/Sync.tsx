import React from 'react';
import { Button, } from 'antd';
import { SyncOutlined } from '@ant-design/icons';

interface Props {
  process: {
    chrome: any[],
    telegram: any[]
  }
}

const Sync: React.FC<Props> = ({ process }) => {
  const { chrome } = process;
  const noMoreChromeOpen = chrome.length < 2;
  const handleSyncClick = async () => {
    const res = await window.py.sync.start()
    if (res.success) {
      window.message.success(res.message)
    }else{
      window.message.error(res.error)
    }
  };

  return (
    <>
      <Button
        size="large"
        disabled={noMoreChromeOpen}
        onClick={handleSyncClick}
      >
        同步
      </Button>
    </>
  );
};

export default Sync;