import React, { useState } from 'react';
import { Button, Modal } from 'antd';
import { SyncOutlined } from '@ant-design/icons';
import AutoSync from './AutoSync';

interface Props {
  selectedRows: any[];
}

const Sync: React.FC<Props> = ({ selectedRows }) => {
  const [autoSyncVisible, setAutoSyncVisible] = useState(false);

  const handleSyncClick = () => {
    if (selectedRows.length === 0) {
      window.message.warning('请先选择Chrome实例');
      return;
    }
    setAutoSyncVisible(true);
  };

  return (
    <>
      <Button
        size="large"
        icon={<SyncOutlined />}
        onClick={handleSyncClick}
      >
        同步
      </Button>

      <Modal
        title="Chrome自动同步"
        open={autoSyncVisible}
        onCancel={() => setAutoSyncVisible(false)}
        footer={null}
        width={700}
        destroyOnClose
      >
        <AutoSync selectedRows={selectedRows} />
      </Modal>
    </>
  );
};

export default Sync;