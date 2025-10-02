import React from 'react';
import { Button, Tooltip, } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { useInterval, } from 'ahooks'

interface Props {
  isSync: boolean
  setIsSync: (value: boolean) => void
  process: {
    chrome: any[],
    telegram: any[]
  }
}

const Sync: React.FC<Props> = ({ process, isSync, setIsSync }) => {
  const { chrome, } = process;
  const noMoreChromeOpen = chrome.length < 2;
  const handleSyncClick = async () => {
    const res = await window.py.sync.start()
    if (res.success) {
      window.message.success(res.message)
      setIsSync(true)
    } else {
      window.message.error(res.error)
    }
  };
  const handleStop = () => {
    window.py.sync.stop()
    setIsSync(false)
    window.message.success("同步已取消")
  }

  // 每3秒检查一次进程是否存在
  useInterval(async () => {
    const res = await window.py.sync.get_sync_status()
    setIsSync(res.data)
  }, 3000)

  return (
    <>
      {
        isSync ?
          <Button
            size="large"
            onClick={handleStop}
            danger
          >
            停止同步
          </Button>
          :
          <Button
            size="large"
            disabled={noMoreChromeOpen || isSync}
            onClick={handleSyncClick}
          >
            同步
          </Button>
      }

      <Tooltip title='开启同步操作，鼠标点击或键盘输入前尽量微微停顿一下鼠标'><QuestionCircleOutlined /></Tooltip>
    </>
  );
};

export default Sync;