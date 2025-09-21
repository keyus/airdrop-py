import { Dropdown, } from 'antd'
import { PoweroffOutlined, } from '@ant-design/icons'

interface Props {
    onOk: () => void
}

export default function Close(props: Props) {
    const { onOk } = props
    const onCloseChrome = async () => {
        await window.pywebview.api.close_chrome_all()
        window.message.success('chrome,关闭成功')
        onOk()
    }

    const onCloseTelegram = async () => {
        await window.pywebview.api.close_tg_all()
        window.message.success('telegram,关闭成功')
        onOk()
    }

    return (
        <Dropdown.Button
            size='large'
            menu={{
                items: [
                    {
                        label: '关闭 Telegram',
                        key: '1',
                        onClick: onCloseTelegram
                    },
                ]
            }}
            onClick={onCloseChrome}>
            <PoweroffOutlined /> 关闭 chrome
        </Dropdown.Button>
    )
}
