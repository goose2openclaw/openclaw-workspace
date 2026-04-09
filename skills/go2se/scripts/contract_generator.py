#!/usr/bin/env python3
"""
GO2SE Smart Contract Generator
代币合约生成器 - 生成ERC20/BEP20/SPL代币
"""

import random

class ContractGenerator:
    """智能合约生成器"""
    
    def __init__(self):
        self.templates = {
            "erc20": self.generate_erc20,
            "bep20": self.generate_bep20,
            "spl": self.generate_spl
        }
    
    def generate_erc20(self, name: str, symbol: str, supply: int) -> str:
        """生成ERC20合约"""
        return f'''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract {symbol} is ERC20, ERC20Burnable, Ownable {{
    uint256 public constant MAX_SUPPLY = {supply} * 10**18;
    
    constructor() ERC20("{name}", "{symbol}") Ownable(msg.sender) {{
        _mint(msg.sender, MAX_SUPPLY);
    }}
    
    function mint(address to, uint256 amount) public onlyOwner {{
        require(totalSupply() + amount <= MAX_SUPPLY, "Max supply exceeded");
        _mint(to, amount);
    }}
    
    function burn(uint256 amount) public override {{
        super.burn(amount);
    }}
}}'''
    
    def generate_bep20(self, name: str, symbol: str, supply: int) -> str:
        """生成BEP20合约"""
        return f'''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract {symbol}BEP20 is ERC20, ERC20Burnable, Ownable {{
    uint256 public constant MAX_SUPPLY = {supply} * 10**18;
    address public marketingWallet;
    uint256 public taxFee = 2;
    
    constructor(address _marketing) ERC20("{name}", "{symbol}") Ownable(msg.sender) {{
        marketingWallet = _marketing;
        _mint(msg.sender, MAX_SUPPLY);
    }}
    
    function transferWithTax(address to, uint256 amount) public {{
        uint256 taxAmount = amount * taxFee / 100;
        _transfer(msg.sender, marketingWallet, taxAmount);
        _transfer(msg.sender, to, amount - taxAmount);
    }}
    
    function mint(address to, uint256 amount) external onlyOwner {{
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }}
}}'''
    
    def generate_spl(self, name: str, symbol: str, supply: int) -> str:
        """生成Solana SPL代币"""
        return f'''// SPL Token: {name} ({symbol})
// Total Supply: {supply} tokens

use solana_program::{{
    entrypoint,
    program_error,
    program_option,
    pubkey::Pubkey,
}};

use solana_program::program_option::COption;
use spl_token::{{
    instruction::{{initialize_mint, initialize_account, mint_to, transfer}},
    state::{{Account, Mint}},
}};

// Token Meta
const NAME: &str = "{name}";
const SYMBOL: &str = "{symbol}";
const DECIMALS: u8 = 9;
const SUPPLY: u64 = {supply};

#[derive(Debug, Clone)]
pub struct TokenData {{
    pub mint: Pubkey,
    pub supply: u64,
    pub decimals: u8,
}}

impl TokenData {{
    pub fn new(mint: Pubkey) -> Self {{
        Self {{
            mint,
            supply: SUPPLY,
            decimals: DECIMALS,
        }}
    }}
}}

entrypoint!(process_instruction);
'''
    
    def generate(self, chain: str, name: str, symbol: str, supply: int = 1000000000) -> str:
        """生成合约"""
        if chain not in self.templates:
            return "Error: Unsupported chain"
        
        return self.templates[chain](name, symbol, supply)
    
    def run(self):
        """运行"""
        print("\n" + "="*60)
        print("🔧 GO2SE 智能合约生成器")
        print("="*60)
        
        print("\n📋 支持的链:")
        for chain in self.templates:
            print(f"   • {chain.upper()}")
        
        print("\n📝 示例合约:")
        
        # ERC20
        print("\n[ERC20 Example]")
        erc20 = self.generate("erc20", "GO2SE Token", "GO2SE", 1000000000)
        print(erc20[:500] + "...")
        
        # BEP20
        print("\n\n[BEP20 Example]")
        bep20 = self.generate("bep20", "GO2SE BEP20", "GO2SE", 1000000000)
        print(bep20[:500] + "...")
        
        # SPL
        print("\n\n[SPL Example]")
        spl = self.generate("spl", "GO2SE Solana", "GO2SE", 1000000000)
        print(spl[:500] + "...")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    ContractGenerator().run()
