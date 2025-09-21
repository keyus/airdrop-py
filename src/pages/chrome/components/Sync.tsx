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
  const handleSyncClick = () => {
    window.py.sync.start()
  };

  return (
    <>
      <Button
        size="large"
        icon={<SyncOutlined />}
        disabled={noMoreChromeOpen}
        onClick={handleSyncClick}
      >
        同步
      </Button>
    </>
  );
};

export default Sync;