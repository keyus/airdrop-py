

import { Button, Space } from 'antd'
import ChromeIcon from '@/assets/chrome.svg?react'
import TelegramIcon from '@/assets/telegram.svg?react'
import CloseIcon from '@/assets/close.svg?react'


type Props = {
    selectedRows: any[]
    onOk: () => void,
    process: {
        chrome: any[],
        telegram: any[],
    }
}

export default function Tools(props: Props) {
    const { selectedRows, onOk, process } = props;

    const hasChromeOpen = process.chrome.length > 0;
    const hasTelegramOpen = process.telegram.length > 0;
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
        window.py.sync.stop()
        await window.py.app.close_chrome_all();
        window.message.success('chrome,关闭成功,同步已关闭')
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
                    disabled={!hasChromeOpen}
                    icon={<CloseIcon width={20} style={{color: hasChromeOpen ? 'red': '#aaa'}}/>}
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
                    disabled={!hasTelegramOpen}
                    onClick={onCloseTelegram}
                    icon={<CloseIcon width={20}  style={{color: hasTelegramOpen ? 'red': '#aaa'}} />} />
            </Space.Compact>

        </>
    )
}
