

import { Button, Space } from 'antd'
import { CloseOutlined } from '@ant-design/icons'
import ChromeIcon from '@/assets/chrome.svg?react'
import TelegramIcon from '@/assets/telegram.svg?react'


type Props = {
    selectedRows: any[]
    onOk: () => void
}

export default function Tools(props: Props) {
    const { selectedRows, onOk } = props

    const onOpenChrome = async () => {
        const names = selectedRows.map(it => it.name)
        await window.py.app.open_chrome(names)
        window.message.success('chrome,打开成功')
        onOk()
    }

    const onOpenTelegram = async () => {
        const names = selectedRows.map(it => it.name)
        await window.py.app.open_telegram(names)
        window.message.success('telegram,打开成功')
        onOk()
    }
    const onCloseChrome = async () => {
        await window.py.app.close_chrome_all();
        window.message.success('chrome,关闭成功')
        onOk()
    }

    const onCloseTelegram = async () => {
        await window.py.app.close_telegram_all();
        window.message.success('telegram,关闭成功')
        onOk()
    }

    return (
        <>
            <Space.Compact>
                <Button
                    disabled={selectedRows.length === 0}
                    size='large'
                    onClick={onOpenChrome}
                    icon={<ChromeIcon width={20} />} />
                <Button
                    size='large'
                    onClick={onCloseChrome}
                    icon={<CloseOutlined />}
                />
            </Space.Compact>
            <Space.Compact>
                <Button
                    disabled={selectedRows.length === 0}
                    size='large'
                    onClick={onOpenTelegram}
                    icon={<TelegramIcon width={20} />} />
                <Button
                    size='large'
                    onClick={onCloseTelegram}
                    icon={<CloseOutlined />} />
            </Space.Compact>

        </>
    )
}
